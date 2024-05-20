import PropTypes from "prop-types";

function User({ user }) {
  return (
    <div className="user">
      <img
        src={
          user.profile_pic
            ? user.profile_pic
            : "https://i.imgur.com/tdi3NGag.jpg"
        }
        alt="user_profile_pic"
        style={{ width: 128, height: 128 }}
      />
      <div className="username">@{user.user_name}</div>
      <div className="displayName">{user.display_name}</div>
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
};

export default User;
