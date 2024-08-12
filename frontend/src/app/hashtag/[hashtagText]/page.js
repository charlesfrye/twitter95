import HashtagFeed from '../../../components/HashtagFeed';

export default function HashtagPage({ params }) {
  return (
    <HashtagFeed hashtagText={params.hashtagText} />
  );
}