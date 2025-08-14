import React from 'react';
import { TOKENS } from '../styles/tokens';
import { Card, Btn } from './Primitives';

interface UnifiedNavigationProps {
  activeRoute: string;
  onNavigate: (route: string, id: string) => void;
}

export const UnifiedNavigation: React.FC<UnifiedNavigationProps> = ({
  activeRoute,
  onNavigate,
}) => {
  return (
    <Card pad={12}>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <div style={{display:'flex', gap:12, alignItems:'center'}}>
          <img src="yaz://assets/logo.svg" height={20} />
          <strong style={{color:TOKENS.text}}>Yaz Surge</strong>
        </div>
        <div style={{display:'flex', gap:8}}>
          <Btn onClick={()=>location.assign('/surge')}>Dashboard</Btn>
          <Btn onClick={()=>location.assign('/surge/cases')}>Cases</Btn>
          <Btn onClick={()=>location.assign('/surge/datasets')}>Datasets</Btn>
        </div>
      </div>
    </Card>
  );
};

export default UnifiedNavigation;
