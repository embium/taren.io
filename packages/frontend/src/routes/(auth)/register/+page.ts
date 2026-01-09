import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	// Client-side auth check will be handled in the component
	return {};
};
