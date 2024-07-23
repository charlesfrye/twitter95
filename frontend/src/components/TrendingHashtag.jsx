function TrendingHashtag({ text }) {
  return (
    <div className="text-[#7FEE64] text-sm">
      <a href={`/hashtag/${text.slice(1)}`} className="text-sm">
        {text}
      </a>
    </div>
  );
}

export default TrendingHashtag;
