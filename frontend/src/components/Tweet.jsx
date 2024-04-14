import PropTypes from "prop-types";

function Tweet({ tweet }) {
  return (
    <div className="tweet">
      <div className="tweetText">{tweet.text}</div>
    </div>
  );
}

Tweet.propTypes = {
  tweet: PropTypes.shape({
    id: PropTypes.string,
    text: PropTypes.string,
    media: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(PropTypes.string),
    ]),
    author: PropTypes.string, // User:id or User object?
    root: PropTypes.string, // Tweet:id or Tweet object?
    // quotedBy: PropTypes.string, // User:id or User object?
    // retweetedBy: PropTypes.string, // User:id or User object?
    quoted: PropTypes.string, // Tweet:id or Tweet object?
    retweeted: PropTypes.string, // Tweet:id or Tweet object?
    likedBy: PropTypes.arrayOf(PropTypes.string),
    timestamp: PropTypes.string,
    userId: PropTypes.string,
  }),
};

export default Tweet;
