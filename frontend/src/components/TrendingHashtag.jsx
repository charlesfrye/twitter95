import { useNavigate } from "react-router-dom";

function TrendingHashtag({ text }) {
  const navigate = useNavigate();

  function handleClick() {
    navigate(`/hashtag/${text.slice(1)}`);
  }

  return (
    <div className="text-[#7FEE64] text-sm cursor-pointer">
      <a onClick={handleClick} className="text-sm">
        {text}
      </a>
    </div>
  );
}

export default TrendingHashtag;
