"use client"

import { useRouter } from "next/navigation";

function RichText({ text }) {
  const router = useRouter();
  const hashtagRegex = /(#\w+)/g; // match on # followed by 1 or more letters, numbers, or underscores
  const usernameRegex = /(@[\w]+)/g; // match on @ followed by 1 or more letters, numbers, or underscores
  const urlRegex = /(https?:\/\/[^\s]+)/g; // match on http(s) followed by :// and non-whitespace characters

  const parts = text.split(/(#\w+|@\w+|https?:\/\/[^\s]+)/);

  function handleHashtagClick(hashtag) {
    router.push(`/hashtag/${hashtag}`);
  }

  function handleUsernameClick(username) {
    router.push(`/profile/${username}`);
  }

  return parts.map((part, index) => {
    if (part.match(urlRegex)) {
      const displayText =
        part.replace(/^https?:\/\/(www\.)?/, "").slice(0, 33) + // update bot logic if you change URL display len
        (part.length > 33 ? "..." : "");
      return (
        <a
          key={index}
          href={part}
          className="text-[#008080] underline hover:text-[#00abab]"
        >
          {displayText}
        </a>
      );
    } else if (part.match(hashtagRegex)) {
      const hashtag = part.slice(1);
      return (
        <a
          key={index}
          onClick={() => handleHashtagClick(hashtag)}
          className="text-[#008080] underline hover:text-[#00abab]"
        >
          {part}
        </a>
      );
    } else if (part.match(usernameRegex)) {
      const username = part.slice(1);
      return (
        <a
          key={index}
          onClick={() => handleUsernameClick(username)}
          className="text-[#008080] underline hover:text-[#00abab]"
        >
          {part}
        </a>
      );
    }
    return part;
  });
}

export default RichText;
