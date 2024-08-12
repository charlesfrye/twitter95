// src/components/TweetPageClient.js
'use client';

import TweetPage from './TweetPage';

export default function TweetPageClient({ tweetData }) {
  return (
    <TweetPage tweetData={tweetData} />
  );
}