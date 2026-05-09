<script>
  import { onMount } from 'svelte';
  import { supabase, signInWithPassword, signUp, signOut, onAuthStateChange } from '../lib/supabase.js';
  import { appState } from '../stores/app.js';
  import { ca } from '../lib/i18n.js';
  const t = ca;

  let loading = false;
  let error = null;
  let appStateValue = null;
  let email = '';
  let password = '';
  let isSignUp = false;

  appState.subscribe(value => { appStateValue = value; });

  onMount(() => {
    const { data: { subscription } } = onAuthStateChange((event, session) => {
      if (session?.user) {
        appState.update(state => ({
          ...state,
          isAuthenticated: true,
          user: {
            id: session.user.id,
            email: session.user.email,
            name: session.user.user_metadata?.full_name || session.user.email,
            picture: session.user.user_metadata?.avatar_url || null
          }
        }));
      } else {
        appState.update(state => ({
          ...state,
          isAuthenticated: false,
          user: null
        }));
      }
    });

    return () => subscription.unsubscribe();
  });

  async function handleSubmit() {
    if (!email || !password) {
      error = 'OMPLIU TOTS ELS CAMPS';
      return;
    }

    loading = true;
    error = null;

    try {
      if (isSignUp) {
        const { error: signUpError } = await signUp(email, password);
        if (signUpError) {
          error = signUpError.message || 'REGISTRE FALLIT';
        } else {
          error = 'REVISA EL TEU EMAIL PER CONFIRMAR';
        }
      } else {
        const { error: signInError } = await signInWithPassword(email, password);
        if (signInError) {
          error = signInError.message || 'CONNEXIÓ FALLIDA';
        } else {
          window.location.href = '/';
        }
      }
    } catch (err) {
      error = err.message || 'ERROR';
    } finally {
      loading = false;
    }
  }

  async function handleLogout() {
    loading = true;
    try {
      await signOut();
      appState.update(state => ({ ...state, isAuthenticated: false, user: null }));
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      loading = false;
    }
  }

  function toggleMode() {
    isSignUp = !isSignUp;
    error = null;
  }
</script>

<div class="w-full py-4">
  {#if appStateValue?.isAuthenticated && appStateValue?.user}
    <div class="flex flex-col items-center gap-4">
      <div class="w-20 h-20 rounded-full overflow-hidden bg-surface-2 border-2 border-border">
        {#if appStateValue.user.picture}
          <img src={appStateValue.user.picture} alt="" class="w-full h-full object-cover" />
        {:else}
          <div class="w-full h-full flex items-center justify-center">
            <svg class="w-10 h-10 text-tertiary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="8" r="4"/>
              <path d="M4 20c0-4 4-6 8-6s8 2 8 6"/>
            </svg>
          </div>
        {/if}
      </div>

      <div class="text-center">
        <h2 class="font-mono text-lg font-semibold text-primary tracking-wide">
          {appStateValue.user.name || appStateValue.user.email}
        </h2>
        <p class="font-mono text-xs text-secondary tracking-wider">{appStateValue.user.email}</p>
      </div>

      <div class="w-full bg-surface-2 border-2 border-border p-4">
        <h3 class="font-mono text-xs font-semibold text-accent-main tracking-widest uppercase mb-3">{t.auth.connected}</h3>
        <div class="flex flex-col gap-2">
          <div class="flex justify-between">
            <span class="font-mono text-xs text-secondary tracking-wider">ID</span>
            <span class="font-mono text-xs text-tertiary">{appStateValue.user.id.slice(0, 8)}...</span>
          </div>
        </div>
      </div>

      <button
        class="px-4 py-2 border-2 border-error text-error font-mono text-xs font-semibold tracking-wider hover:bg-error hover:text-surface transition-all"
        on:click={handleLogout}
        disabled={loading}
      >
        {t.auth.disconnect}
      </button>
    </div>
  {:else}
    <div class="flex flex-col items-center gap-4">
      <div class="w-20 h-20 bg-surface-2 border-2 border-border flex items-center justify-center">
        <svg class="w-10 h-10 text-tertiary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="8" r="4"/>
          <path d="M4 20c0-4 4-6 8-6s8 2 8 6"/>
        </svg>
      </div>

      <h2 class="font-mono text-lg font-semibold text-primary tracking-wide">
        {isSignUp ? 'CREA UN COMPTE' : 'INICIAR SESSIÓ'}
      </h2>

      <form class="w-full max-w-[300px] flex flex-col gap-3" on:submit|preventDefault={handleSubmit}>
        {#if error}
          <div class="text-error font-mono text-xs tracking-wider text-center p-2 bg-error/10 border-2 border-error">
            {error}
          </div>
        {/if}

        <input
          type="email"
          bind:value={email}
          placeholder="EMAIL"
          class="w-full px-3 py-2 bg-surface-2 border-2 border-border text-primary font-mono text-sm focus:border-accent-main outline-none"
        />

        <input
          type="password"
          bind:value={password}
          placeholder="CONTRASENYA"
          class="w-full px-3 py-2 bg-surface-2 border-2 border-border text-primary font-mono text-sm focus:border-accent-main outline-none"
        />

        <button
          type="submit"
          class="w-full px-4 py-3 bg-accent-main text-surface font-mono text-xs font-semibold tracking-wider disabled:opacity-50"
          disabled={loading}
        >
          {loading ? '...' : isSignUp ? 'CREAR COMPTE' : 'ENTRAR'}
        </button>
      </form>

      <button
        class="text-secondary font-mono text-xs tracking-wider hover:text-accent-main transition-colors"
        on:click={toggleMode}
      >
        {isSignUp ? 'JA TENS COMPTE? ENTRA' : 'NO TENS COMPTE? REGISTRA\'T'}
      </button>
    </div>
  {/if}
</div>