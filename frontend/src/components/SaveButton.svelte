// frontend/src/components/SaveButton.svelte
<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();
  let loading = false;
  let successMessage = null;
  let errorMessage = null;

  async function handleSave(invoiceData) {
    loading = true;
    successMessage = null;
    errorMessage = null;

    try {
      // Dispatch save request to parent component
      dispatch('save-invoice', invoiceData);

      // Simulate API call - in real app, this would be handled by parent
      // For now, we'll simulate success after a delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Simulate successful save
      successMessage = 'Invoice saved successfully!';
      loading = false;

      // Clear success message after 3 seconds
      setTimeout(() => {
        successMessage = null;
      }, 3000);
    } catch (error) {
      console.error('Save error:', error);
      errorMessage = 'Failed to save invoice. Please try again.';
      loading = false;
    }
  }

  function resetMessages() {
    successMessage = null;
    errorMessage = null;
  }
</script>

<div class="save-button-container">
  {#if loading}
    <button type="submit" disabled class="save-button loading">
      Saving...
    </button>
  {:else}
    <button type="submit" class="save-button" on:click|preventDefault={() => handleSave(formData)}>
      Save Invoice
    </button>
  {/if}

  {#if successMessage}
    <div class="message success">
      {successMessage}
    </div>
  {/if}

  {#if errorMessage}
    <div class="message error">
      {errorMessage}
    </div>
  {/if}
</div>

<style>
  .save-button-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 2rem;
  }

  .save-button {
    padding: 0.75rem 2rem;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .save-button:hover:not(:disabled) {
    background-color: #218838;
  }

  .save-button:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
  }

  .save-button.loading::after {
    content: '';
    position: relative;
    width: 1rem;
    height: 1rem;
    border: 2px solid #ffffff;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-left: 0.5rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .message {
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    margin-top: 1rem;
    display: flex;
    align-items: center;
    min-width: 200px;
    justify-content: center;
  }

  .message.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }

  .message.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
</style>