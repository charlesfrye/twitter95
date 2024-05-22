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

function Tweet({ tweet }) {
  const navigate = useNavigate();
  const author = tweet.author;

  const handleClick = () => {
    navigate(`/profile/${author.user_id}`);
  };

  console.log(tweet);

  return (
    tweet && (
      <div className="tweet">
        <MenuList className="!flex !flex-col text-ellipsis">
          <MenuListItem
            className="!cursor-pointer !text-sm !overflow-hidden !whitespace-nowrap !text-ellipsis"
            onClick={handleClick}
          >
            {author.profile_pic && (
              <img
                src={author.profile_pic}
                alt={author.user_name}
                style={{ width: 30, height: 30 }}
              />
            )}
            {`@${author.user_name} on ${formatFakeTime(tweet.fake_time)}`}
          </MenuListItem>
          <Separator />
          <MenuListItem
            size="sm"
            onClick={handleClick}
            className="!whitespace-normal !text-left !cursor-pointer !min-h-48"
          >
            {tweet.text}
          </MenuListItem>
          {tweet.quoted && tweet.quoted_tweet && (
            <Tweet tweet={tweet.quoted_tweet} />
          )}
        </MenuList>
      </div>
    )
  );
}

Tweet.propTypes = {
  tweet: PropTypes.shape({
    author: PropTypes.shape({
      user_id: PropTypes.number,
      user_name: PropTypes.string,
      display_name: PropTypes.string,
      profile_pic: PropTypes.string,
    }),
    tweet_id: PropTypes.number,
    text: PropTypes.string,
    fake_time: PropTypes.string,
    author_id: PropTypes.number,
    quoted: PropTypes.number,
    quoted_tweet: PropTypes.object, // recursive, depth 1
  }),
};

export default Tweet;
