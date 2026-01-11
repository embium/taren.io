<script lang="ts">
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
  import { setMode, mode } from 'mode-watcher';
  import { Sun, MoonStar } from '@lucide/svelte';

  function handleThemeClick(theme: 'light' | 'dark') {
    setMode(theme);
  }
</script>

<DropdownMenu.Label>
  <span class="flex items-center justify-between w-full">
    <span>Theme</span>
    <span class="flex items-center gap-1 rounded-full border border-[#262626] p-1">
      <button
        onclick={(e) => {
          e.stopPropagation();
          handleThemeClick('light');
        }}
        class="rounded-full p-1.5 transition-colors {mode.current === 'light' ? 'bg-gray-900 dark:bg-[#fafafa]' : 'hover:bg-gray-100 dark:hover:bg-[#262626]'}"
        aria-label="Light mode"
      >
        <Sun class={mode.current === 'light' ? 'text-white dark:text-[#0a0a0a]' : 'text-gray-900 dark:text-[#fafafa]'} size={16} />
      </button>
      <button
        onclick={(e) => {
          e.stopPropagation();
          handleThemeClick('dark');
        }}
        class="rounded-full p-1.5 transition-colors {mode.current === 'dark' ? 'bg-gray-900 dark:bg-[#fafafa]' : 'hover:bg-gray-100 dark:hover:bg-[#262626]'}"
        aria-label="Dark mode"
      >
        <MoonStar class={mode.current === 'dark' ? 'text-white dark:text-[#0a0a0a]' : 'text-gray-900 dark:text-[#fafafa]'} size={16} />
      </button>
    </span>
  </span>
</DropdownMenu.Label>