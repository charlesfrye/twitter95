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
    id: PropTypes.string, // user:id
    content: PropTypes.string,
    location: PropTypes.shape({
      lat: PropTypes.number,
      long: PropTypes.number,
    }),
    birthdate: PropTypes.string,
    dateJoined: PropTypes.string,
  }),
};

export default Bio;
