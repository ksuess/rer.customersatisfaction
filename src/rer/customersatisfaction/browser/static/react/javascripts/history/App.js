import React, { useState } from 'react';
import TranslationsWrapper from '../TranslationsContext';
import ApiWrapper from '../ApiContext';
import Menu from './Menu/Menu';
import CustomerSatisfactionList from './CustomerSatisfactionList';
import './App.less';

const App = () => {
  const [user, setUser] = useState(null);

  const endpoint = 'customer-satisfaction';

  const children = (
    <React.Fragment>
      <Menu />
      <CustomerSatisfactionList />
    </React.Fragment>
  );

  return (
    <TranslationsWrapper>
      <ApiWrapper endpoint={endpoint}>{children}</ApiWrapper>
    </TranslationsWrapper>
  );
};
export default App;
