import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MenuList, MenuListItem, Separator } from "react95";
import { getUser } from "../services/database";

function Tweet({ tweet }) {
  const navigate = useNavigate();
  const [user, setUser] = useState({});

  useEffect(() => {
    async function fetchUser() {
      try {
        const fetchedUser = await getUser(tweet.author_id);
        console.log(fetchedUser);
        setUser(fetchedUser);
      } catch (error) {
        console.error("Failed to fetch user:", error);
      }
    }
    fetchUser();
  }, [tweet.author_id]);

  const handleClick = () => {
    navigate(`/profile/${user.user_id}`);
  };

  return (
    <div className="tweet">
      <MenuList>
        <MenuListItem
          size="sm"
          onClick={handleClick}
          style={{ width: "500px", textOverflow: "wrap", overflow: "scroll" }}
        >
          🎤 {tweet.text}
        </MenuListItem>
        <Separator />
        <MenuListItem onClick={handleClick}>
          {user.profile_pic && (
            <img
              src={user.profile_pic}
              alt="User"
              style={{ width: 30, height: 30, borderRadius: "50%" }}
            />
          )}
          {user.display_name || user.user_id}
        </MenuListItem>
        <div className="tweetMedia">
          {Array.isArray(tweet.images) ? (
            tweet.images.map((image, index) => (
              <img
                key={index}
                src={image}
                alt="Media"
                style={{ width: "100%", height: "auto" }}
              />
            ))
          ) : tweet.images ? (
            <img
              src={tweet.images}
              alt="Media"
              style={{ width: "100%", height: "auto" }}
            />
          ) : null}
        </div>
      </MenuList>
      <Separator />
      <div className="tweetfakeTime">
        <p>Posted at {tweet.fake_time}</p>
      </div>
      {/* <div className="tweetRoot">
        {tweet.root !== tweet.tweet_id && (
          <div className="tweetRoot">
            <p>Root tweet text: {tweet.root}</p>
          </div>
        )}
      </div> */}
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
        {tweet.liked_by && (
          <div className="tweetLikedBy">
            <p>Likes {tweet.liked_by}</p>
          </div>
        )}
      </div>
    </div>
  );
}

Tweet.propTypes = {
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
    real_time: PropTypes.number,
  }),
};

export default Tweet;
