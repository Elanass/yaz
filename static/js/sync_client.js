// sync_client.js

// IndexedDB setup
const dbPromise = indexedDB.open("offline-edits", 1);
dbPromise.onupgradeneeded = (event) => {
  const db = event.target.result;
  db.createObjectStore("edits", { keyPath: "id" });
};

// Listen for offline edits
function saveOfflineEdit(edit) {
  dbPromise.onsuccess = (event) => {
    const db = event.target.result;
    const transaction = db.transaction("edits", "readwrite");
    const store = transaction.objectStore("edits");
    store.add(edit);
  };
}

// --- CRDT merge logic ---
function crdtMerge(local, remote) {
  // Example: RGA merge for text, last-write-wins for JSON
  if (local.type === 'text') {
    // Merge arrays of {id, char, visible}
    const byId = {};
    [...local.data, ...remote.data].forEach(e => {
      if (!byId[e.id]) byId[e.id] = {...e};
      else byId[e.id].visible = byId[e.id].visible || e.visible;
    });
    return { type: 'text', data: Object.values(byId).sort((a, b) => a.id.localeCompare(b.id)) };
  } else {
    // JSON: last-write-wins
    return { type: 'json', data: { ...local.data, ...remote.data } };
  }
}

// --- Sync logic ---
async function sendMessages() {
  const edits = await getOfflineEdits();
  if (edits.length === 0) return;
  const response = await fetch("/message/send", {
    method: "POST",
    body: JSON.stringify({ edits }),
    headers: { "Content-Type": "application/json" },
  });
  if (response.ok) clearOfflineEdits();
}

async function syncMessages() {
  // Get remote deltas
  const response = await fetch("/message/sync");
  const remote = await response.json();
  // Get local state
  const local = window.currentCRDTState || { type: 'text', data: [] };
  // Merge via CRDT
  const merged = crdtMerge(local, remote);
  window.currentCRDTState = merged;
  // Update UI (example)
  if (merged.type === 'text') {
    document.getElementById('case-detail').innerText = merged.data.map(e => e.visible ? e.char : '').join('');
  }
}

// Poll and merge via CRDT
async function syncMessages() {
  const response = await fetch("/message/sync");
  const messages = await response.json();
  mergeMessages(messages);
}

function getOfflineEdits() {
  return new Promise((resolve) => {
    dbPromise.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction("edits", "readonly");
      const store = transaction.objectStore("edits");
      const edits = [];
      store.openCursor().onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor) {
          edits.push(cursor.value);
          cursor.continue();
        } else {
          resolve(edits);
        }
      };
    };
  });
}

function clearOfflineEdits() {
  dbPromise.onsuccess = (event) => {
    const db = event.target.result;
    const transaction = db.transaction("edits", "readwrite");
    const store = transaction.objectStore("edits");
    store.clear();
  };
}

function mergeMessages(messages) {
  console.log("Merged messages:", messages);
}

// Periodic sync
setInterval(() => {
  if (navigator.onLine) {
    sendMessages();
    syncMessages();
  }
}, 3000);

// Expose for UI test
window.saveOfflineEdit = saveOfflineEdit;
window.getOfflineEdits = getOfflineEdits;
window.clearOfflineEdits = clearOfflineEdits;
window.crdtMerge = crdtMerge;
