import "./Tweet.css";
import PropTypes from "prop-types";

function TweetContent({ tweet }) {
  const renderText = (text) => {
    const hashtagRegex = /(#\w+)/g; // match on # followed by 1 or more letters, numbers, or underscores
    const usernameRegex = /(@[\w]+)/g; // match on @ followed by 1 or more letters, numbers, or underscores
    const urlRegex = /(https?:\/\/[^\s]+)/g; // match on http(s) followed by :// and non-whitespace characters

    const parts = text.split(/(#\w+|@\w+|https?:\/\/[^\s]+)/);

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
            href={`/hashtag/${hashtag}`}
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
            href={`/profile/${username}`}
            className="text-[#008080] underline hover:text-[#00abab]"
          >
            {part}
          </a>
        );
      }
      return part;
    });
  };

  return tweet && <div className="tweet-content">{renderText(tweet.text)}</div>;
}

TweetContent.propTypes = {
  tweet: PropTypes.shape({
    author: PropTypes.shape({
      user_id: PropTypes.number,
      user_name: PropTypes.string,
      display_name: PropTypes.string,
      profile_pic: PropTypes.string,
    }),
    tweet_id: PropTypes.number,
    text: PropTypes.string,
    likes: PropTypes.number,
    quotes: PropTypes.number,
    fake_time: PropTypes.string,
    author_id: PropTypes.number,
    quoted: PropTypes.number,
    quoted_tweet: PropTypes.object, // recursive, depth 1
  }),
};

export default TweetContent;
