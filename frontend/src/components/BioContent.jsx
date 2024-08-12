"use client";

import RichText from "./RichText";

function BioContent({ bio }) {
  return (
    bio && (
      <div className="user-bio text-white text-xl">
        <RichText text={bio.content} />
      </div>
    )
  );
}

export default BioContent;
