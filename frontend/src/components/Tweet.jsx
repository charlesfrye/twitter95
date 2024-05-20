import PropTypes from "prop-types";
import { useNavigate } from "react-router-dom";
import { MenuList, MenuListItem, Separator } from "react95";

function formatFakeTime(fakeTimeStr) {
  const date = new Date(fakeTimeStr);
  const formattedDateTime = new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  }).format(date);

  return formattedDateTime;
}

function Tweet({ authorTweet }) {
  const navigate = useNavigate();
  const user = authorTweet.author;
  const tweet = authorTweet.tweet;

  const handleClick = () => {
    navigate(`/profile/${user.user_id}`);
  };

  return (
    <div className="tweet">
      <MenuList className="!flex !flex-col text-ellipsis">
        <MenuListItem
          size="sm"
          onClick={handleClick}
          className="!whitespace-normal !text-left !cursor-pointer !h-48"
        >
          {tweet.text}
        </MenuListItem>
        <Separator />
        <MenuListItem className="!cursor-pointer gap-4" onClick={handleClick}>
          {user.profile_pic && (
            <img
              src={user.profile_pic}
              alt="User"
              style={{ width: 30, height: 30 }}
            />
          )}
          {`@${user.user_name} on ${formatFakeTime(tweet.fake_time)}`}
        </MenuListItem>
      </MenuList>
    </div>
  );
}

Tweet.propTypes = {
  authorTweet: PropTypes.shape({
    author: PropTypes.shape({
      user_id: PropTypes.number,
      user_name: PropTypes.string,
      display_name: PropTypes.string,
      profile_pic: PropTypes.string,
    }),
    tweet: PropTypes.shape({
      tweet_id: PropTypes.number,
      text: PropTypes.string,
      images: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.arrayOf(PropTypes.string),
      ]),
      author_id: PropTypes.number,
      root: PropTypes.string,
      quoted: PropTypes.string,
      retweeted: PropTypes.string,
      liked_by: PropTypes.arrayOf(PropTypes.number),
      replies: PropTypes.arrayOf(PropTypes.object),
      fake_time: PropTypes.string,
      real_time: PropTypes.string,
    }),
  }),
};

export default Tweet;
