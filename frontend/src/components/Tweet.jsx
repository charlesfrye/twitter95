import PropTypes from "prop-types";

function Tweet({ tweet }) {
  return (
    <div className="tweet">
      <div className="tweetText">{tweet.text}</div>
      <div className="tweetMedia">
        {tweet.media ? (
          <img
            src={tweet.media}
            alt="Media"
            style={{ width: "100%", height: "auto" }}
          />
        ) : null}
      </div>
      <div className="tweetAuthor">
        <p>Posted by {tweet.author}</p>
      </div>
      <div className="tweetfakeTime">
        <p>Posted at {tweet.fakeTime}</p>
      </div>
      <div className="tweetRoot">
        {tweet.root !== tweet.id && (
          <div className="tweetRoot">
            <p>Root tweet text: {tweet.root}</p>
          </div>
        )}
      </div>
      <div className="tweetQuoted">
        {tweet.quoted && (
          <div className="tweetQuoted">
            <p>Quoted tweet text: {tweet.quoted}</p>
          </div>
        )}
      </div>
      <div className="tweetRetweeted">
        {tweet.retweeted && (
          <div className="tweetRetweeted">
            <p>Retweeted tweet text: {tweet.retweeted}</p>
          </div>
        )}
      </div>
      <div className="tweetLikedBy">
        {tweet.likedBy && (
          <div className="tweetLikedBy">
            <p>Liked by: {tweet.likedBy}</p>
          </div>
        )}
      </div>
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
    likedBy: PropTypes.number,
    fakeTime: PropTypes.number,
    realTime: PropTypes.number,
    userId: PropTypes.string,
  }),
};

export default Tweet;
