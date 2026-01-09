import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	// This will be handled by the client-side redirect in the component
	// since we can't access the auth store on the server
	return {};
};
