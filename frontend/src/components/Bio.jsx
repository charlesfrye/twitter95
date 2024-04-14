import PropTypes from "prop-types";

function Bio({ bio }) {
  return (
    <div className="bio">
      <div className="bioContent">{bio.content}</div>
    </div>
  );
}

Bio.propTypes = {
  bio: PropTypes.shape({
    content: PropTypes.string,
    location: PropTypes.string,
    birthday: PropTypes.string,
    joined_on: PropTypes.string,
    user_id: PropTypes.number,
  }),
};

export default Bio;
