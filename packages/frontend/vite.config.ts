import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
const __dirname = dirname(fileURLToPath(import.meta.url));
export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	server: {
		hmr: {
			// Workaround for Svelte 5 HMR issues
			overlay: false
		},
		fs: {
			// Allow serving files from anywhere in the workspace
			allow: [
				// Search up for workspace root
				resolve(__dirname, '../..'),
				// Explicitly allow pnpm store
				resolve(__dirname, '../../node_modules')
			],
			strict: false
		}
	},
	resolve: {
		alias: {
			$lib: resolve(__dirname, 'src/lib')
		}
	}
});
