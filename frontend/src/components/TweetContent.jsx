import "./Tweet.css";
import RichText from "./RichText";
import PropTypes from "prop-types";

function TweetContent({ tweet }) {
  return (
    tweet && (
      <div className="tweet-content">
        <RichText text={tweet.text} />
      </div>
    )
  );
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
