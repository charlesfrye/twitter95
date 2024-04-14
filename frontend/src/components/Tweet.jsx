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
    id: PropTypes.number,
    text: PropTypes.string,
    timestamp: PropTypes.string,
    userId: PropTypes.string,
  }),
};

export default Tweet;
