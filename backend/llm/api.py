import os

import modal

vllm_image = modal.Image.debian_slim(python_version="3.10").pip_install(
    [
        "vllm==0.5.3post1",  # LLM serving
        "huggingface_hub==0.24.1",  # download models from the Hugging Face Hub
        "hf-transfer==0.1.8",  # download models faster
    ]
)

MODEL_NAME = "meta-llama/Meta-Llama-3.1-405B-Instruct-FP8"
MODEL_REVISION = "d8e5bf570eac69f7dfc596cfaaebe6acbf95ca2e"
MODEL_DIR = f"/llamas/{MODEL_NAME}"

MINUTES = 60  # seconds
HOURS = 60 * MINUTES
GIGABYTES = 1024  # megabytes

app = modal.App("vllm-openai-compatible-405b")

N_GPU = 8

volume = modal.Volume.from_name("llamas", create_if_missing=False)


@app.function(
    image=vllm_image,
    gpu=modal.gpu.A100(count=N_GPU, size="80GB"),
    memory=336 * GIGABYTES,  # max
    container_idle_timeout=20 * MINUTES,
    timeout=1 * HOURS,
    allow_concurrent_inputs=100,
    volumes={"/llamas": volume},
    secrets=[modal.Secret.from_name("vllm-secret")],
    keep_warm=1,
    concurrency_limit=1,
)
@modal.asgi_app()
def serve():
    import asyncio

    import fastapi
    import vllm.entrypoints.openai.api_server as api_server
    from vllm.engine.arg_utils import AsyncEngineArgs
    from vllm.engine.async_llm_engine import AsyncLLMEngine
    from vllm.entrypoints.openai.serving_chat import OpenAIServingChat
    from vllm.entrypoints.openai.serving_completion import (
        OpenAIServingCompletion,
    )
    from vllm.entrypoints.logger import RequestLogger
    from vllm.usage.usage_lib import UsageContext

    volume.reload()

    # create a fastAPI app that uses vLLM's OpenAI-compatible router
    app = fastapi.FastAPI(
        title=f"OpenAI-compatible {MODEL_NAME} server",
        description="Run an OpenAI-compatible LLM server with vLLM on modal.com",
        version="0.0.1",
        docs_url="/docs",
    )

    # security: CORS middleware for external requests
    http_bearer = fastapi.security.HTTPBearer(
        scheme_name="Bearer Token", description="See code for authentication details."
    )
    app.add_middleware(
        fastapi.middleware.cors.CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # security: inject dependency on authed routes
    async def is_authenticated(api_key: str = fastapi.Security(http_bearer)):
        if api_key.credentials != os.environ["VLLM_API_KEY"]:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {"username": "authenticated_user"}

    router = fastapi.APIRouter(dependencies=[fastapi.Depends(is_authenticated)])

    router.include_router(api_server.router)
    app.include_router(router)

    engine_args = AsyncEngineArgs(
        model=MODEL_DIR,
        tensor_parallel_size=N_GPU,
        gpu_memory_utilization=0.90,
        max_model_len=2048 + 256,
        enforce_eager=False,
    )

    engine = AsyncLLMEngine.from_engine_args(
        engine_args, usage_context=UsageContext.OPENAI_API_SERVER
    )

    try:  # copied from vLLM -- https://github.com/vllm-project/vllm/blob/507ef787d85dec24490069ffceacbd6b161f4f72/vllm/entrypoints/openai/api_server.py#L235C1-L247C1
        event_loop = asyncio.get_running_loop()
    except RuntimeError:
        event_loop = None

    if event_loop is not None and event_loop.is_running():
        # If the current is instanced by Ray Serve,
        # there is already a running event loop
        model_config = event_loop.run_until_complete(engine.get_model_config())
    else:
        # When using single vLLM without engine_use_ray
        model_config = asyncio.run(engine.get_model_config())

    request_logger = RequestLogger(max_log_len=2048)

    api_server.openai_serving_chat = OpenAIServingChat(
        engine,
        model_config=model_config,
        served_model_names=[MODEL_DIR],
        chat_template=None,
        response_role="assistant",
        lora_modules=[],
        prompt_adapters=[],
        request_logger=request_logger,
    )
    api_server.openai_serving_completion = OpenAIServingCompletion(
        engine,
        model_config=model_config,
        served_model_names=[MODEL_DIR],
        lora_modules=[],
        prompt_adapters=[],
        request_logger=request_logger,
    )

    return app
