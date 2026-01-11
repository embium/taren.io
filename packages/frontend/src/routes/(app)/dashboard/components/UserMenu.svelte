<script lang="ts">
  import { House, LogOut } from '@lucide/svelte';
  import { goto } from '$app/navigation';
  import { getAuthState } from '$lib/stores/auth.svelte';
  import { logout } from '$lib/stores/auth.svelte';
  import { toast } from '$lib/stores/toast.svelte';
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
  import ThemeSelector from './ThemeSelector.svelte';

  const authState = getAuthState();

  async function handleLogout() {
    try {
      await logout();
      toast.success('Logged out successfully');
      goto('/login');
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Logout failed');
    }
  }
</script>

{#if authState.isAuthenticated && authState.user}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      {#snippet child({ props })}
        <button 
          class="w-10 h-10 rounded-full bg-gradient-to-br from-[#b700ff] to-[#00b7ff] flex items-center justify-center text-white font-semibold hover:opacity-90 transition-opacity" 
          {...props}
        >
          {authState.user && authState.user.name ? authState.user.name.charAt(0).toUpperCase() : authState.user?.email.charAt(0).toUpperCase()}
        </button>
      {/snippet}
    </DropdownMenu.Trigger>
    <DropdownMenu.Content class="w-64" align="end">
      <div class="px-3 py-3 mb-1">
        <p class="text-base font-semibold text-gray-900 dark:text-[#fafafa] mb-0.5">
          {authState.user.name || authState.user.email.split('@')[0]}
        </p>
        <p class="text-sm text-gray-500 dark:text-[#737373] truncate">{authState.user.email}</p>
      </div>
      
      <DropdownMenu.Separator />
      
      <DropdownMenu.Item>
        <a href="/dashboard" class="flex w-full">Dashboard</a>
      </DropdownMenu.Item>
      
      <DropdownMenu.Item>
        Account Settings
      </DropdownMenu.Item>
      
      <DropdownMenu.Separator />

      <ThemeSelector />

      <DropdownMenu.Separator />
      
      <DropdownMenu.Item>
        <span class="flex items-center justify-between w-full">
          <a href="/" class="flex w-full">Home Page</a>
          <House />
        </span>
      </DropdownMenu.Item>
      
      <DropdownMenu.Item onclick={handleLogout}>
        <span class="flex items-center justify-between w-full">
          <span>Log Out</span>
          <LogOut />
        </span>
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/if}