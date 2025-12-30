import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';
import { env } from '$env/dynamic/private';

// Lazy-load the database connection to avoid build-time errors
// when DATABASE_URL is not available (it's only needed at runtime)
let _db: ReturnType<typeof drizzle> | null = null;

function getDb() {
	if (!_db) {
		if (!env.DATABASE_URL) {
			throw new Error('DATABASE_URL environment variable is not set');
		}
		const client = postgres(env.DATABASE_URL);
		_db = drizzle(client, { schema });
	}
	return _db;
}

export const db = new Proxy({} as ReturnType<typeof drizzle>, {
	get(_, prop) {
		return getDb()[prop as keyof ReturnType<typeof drizzle>];
	}
});
