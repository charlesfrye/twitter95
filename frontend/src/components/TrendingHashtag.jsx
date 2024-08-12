"use client";

import { useRouter } from 'next/navigation';

function TrendingHashtag({ text }) {
  const router = useRouter();

  function handleClick() {
    router.push(`/hashtag/${text.slice(1)}`);
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
