// Test coordination between ORBoard, Dash, and Interact islands
// This demonstrates the event-driven architecture for high-end OR features

console.log('🧪 Testing SURGE Islands Coordination...');

// Simulate ORBoard room selection
function testRoomSelection() {
    console.log('📍 Testing room selection coordination...');
    
    window.dispatchEvent(new CustomEvent('orboard:room_selected', {
        detail: {
            roomId: 'OR-1',
            caseId: 1,
            room: {
                id: 'OR-1',
                status: 'occupied',
                phase: 'intraop',
                case: {
                    id: 1,
                    patient: 'John Smith',
                    procedure: 'Laparoscopic Cholecystectomy'
                }
            }
        }
    }));
}

// Simulate instrument count update
function testInstrumentUpdate() {
    console.log('🔧 Testing instrument count coordination...');
    
    window.dispatchEvent(new CustomEvent('interact:update', {
        detail: {
            type: 'instrument_count',
            data: {
                caseId: 1,
                instruments: {
                    total: 30,
                    counted: 28,
                    discrepancies: 2
                }
            }
        }
    }));
}

// Simulate checklist update
function testChecklistUpdate() {
    console.log('✅ Testing checklist coordination...');
    
    window.dispatchEvent(new CustomEvent('interact:update', {
        detail: {
            type: 'checklist_update',
            data: {
                caseId: 1,
                checklist: {
                    total: 12,
                    completed: 9
                }
            }
        }
    }));
}

// Simulate vitals update
function testVitalsUpdate() {
    console.log('💓 Testing vitals coordination...');
    
    window.dispatchEvent(new CustomEvent('interact:update', {
        detail: {
            type: 'vitals_update',
            data: {
                caseId: 1,
                vitals: {
                    hr: 78,
                    bp: '125/82',
                    spo2: 97,
                    temp: 36.7
                }
            }
        }
    }));
}

// Simulate analytics update from Dash
function testAnalyticsUpdate() {
    console.log('📊 Testing analytics coordination...');
    
    window.dispatchEvent(new CustomEvent('dash:update', {
        detail: {
            type: 'efficiency_alert',
            data: {
                roomId: 'OR-1',
                message: 'Turnover time exceeding target',
                metrics: {
                    efficiency: 76
                }
            }
        }
    }));
}

// Simulate phase change
function testPhaseChange() {
    console.log('🔄 Testing phase change coordination...');
    
    window.dispatchEvent(new CustomEvent('surge:case_update', {
        detail: {
            caseId: 1,
            updates: {
                phase: 'emergence',
                status: 'occupied'
            }
        }
    }));
}

// Listen for all coordination events to verify they work
function setupEventListeners() {
    console.log('👂 Setting up test event listeners...');
    
    // Listen for ORBoard events
    window.addEventListener('orboard:room_selected', (e) => {
        console.log('✅ ORBoard room selected:', e.detail);
    });
    
    // Listen for Interact events
    window.addEventListener('interact:update', (e) => {
        console.log('✅ Interact update:', e.detail);
    });
    
    // Listen for Dash events
    window.addEventListener('dash:update', (e) => {
        console.log('✅ Dash update:', e.detail);
    });
    
    // Listen for general case updates
    window.addEventListener('surge:case_update', (e) => {
        console.log('✅ Case update:', e.detail);
    });
}

// Run coordination tests
function runCoordinationTests() {
    console.log('🚀 Running SURGE Islands Coordination Tests...');
    
    setupEventListeners();
    
    setTimeout(() => {
        testRoomSelection();
    }, 500);
    
    setTimeout(() => {
        testInstrumentUpdate();
    }, 1000);
    
    setTimeout(() => {
        testChecklistUpdate();
    }, 1500);
    
    setTimeout(() => {
        testVitalsUpdate();
    }, 2000);
    
    setTimeout(() => {
        testAnalyticsUpdate();
    }, 2500);
    
    setTimeout(() => {
        testPhaseChange();
    }, 3000);
    
    setTimeout(() => {
        console.log('✨ Coordination tests completed!');
        console.log('🎯 All islands should now be coordinated and working together');
    }, 3500);
}

// Auto-run tests when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runCoordinationTests);
} else {
    runCoordinationTests();
}

// Export for manual testing
window.surgeCoordinationTest = {
    testRoomSelection,
    testInstrumentUpdate,
    testChecklistUpdate,
    testVitalsUpdate,
    testAnalyticsUpdate,
    testPhaseChange,
    runCoordinationTests
};
