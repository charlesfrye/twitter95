import Profile from '../../../components/Profile';

export default function ProfilePage({ params }) {
  return (
    <Profile userId={params.userID} />
  );
}