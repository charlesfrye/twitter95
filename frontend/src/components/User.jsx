"use client";

import BioContent from "./BioContent";
import PropTypes from "prop-types";

function User({ user, bio }) {
  return (
    <div className="w-[600px] mb-4 flex gap-8 justify-between">
      <img
        src={
          user.profile_pic
            ? user.profile_pic
            : "https://i.imgur.com/tdi3NGag.jpg"
        }
        alt="user_profile_pic"
        style={{ width: 128, height: 128 }}
      />
      <div className="user-info">
        {bio ? <BioContent bio={bio} /> : null}
        <div className="block text-left text-white m-4">
          <div>@{user.user_name}</div>
          <div>{user.display_name}</div>
        </div>
      </div>
    </div>
  );
}

User.propTypes = {
  user: PropTypes.shape({
    user_name: PropTypes.string,
    display_name: PropTypes.string,
    profile_pic: PropTypes.string,
    banner_pic: PropTypes.string,
    user_id: PropTypes.number,
    tweets: PropTypes.arrayOf(PropTypes.object),
  }),
  bio: PropTypes.shape({
    content: PropTypes.string,
  }),
};

export default User;
