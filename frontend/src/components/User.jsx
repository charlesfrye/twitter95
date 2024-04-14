import PropTypes from "prop-types";

function User({ user }) {
  return (
    <div className="user">
      <div className="username">{user.username}</div>
    </div>
  );
}

User.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.string,
    follows: PropTypes.arrayOf(PropTypes.string),
    profilePic: PropTypes.string,
    bannerPic: PropTypes.string,
    username: PropTypes.string,
    displayName: PropTypes.string,
  }),
};

export default User;
