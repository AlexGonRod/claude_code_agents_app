// frontend/src/stores/app.js
import { writable } from 'svelte/store';

export const appState = writable({
    user: null,
    isAuthenticated: false,
    currentImage: null,
    invoiceData: {},
    isProcessing: false,
    isVerifying: false,
    error: null,
    success: null
});

export const authStore = writable({
    token: null,
    user: null,
    isAuthenticated: false
});

export const invoiceStore = writable({
    currentInvoice: {},
    invoices: [],
    loading: false
});