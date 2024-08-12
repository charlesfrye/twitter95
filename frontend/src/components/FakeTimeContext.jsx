"use client";

import React, { createContext, useState } from 'react';
import { fakeNow } from '../services/database';

export const FakeTimeContext = createContext();
export const FakeTimeProvider = ({ children }) => {
  const [fakeTime, setFakeTime] = useState(fakeNow().toISOString());

  return (
    <FakeTimeContext.Provider value={{ fakeTime, setFakeTime }}>
      {children}
    </FakeTimeContext.Provider>
  );
};
