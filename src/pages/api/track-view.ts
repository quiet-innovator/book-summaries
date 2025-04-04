export async function POST({ request }) {
  let slug;
  try {
    const body = await request.json();
    slug = body.slug;
    if (!slug) throw new Error("Missing slug");
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON or missing slug' }), { status: 400 });
  }

  // 🔐 Hardcoded Supabase credentials
  const SUPABASE_URL = 'https://anvbsqdzosqyqggrzsxq.supabase.co';
  const SUPABASE_ANON_KEY =
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFudmJzcWR6b3NxeXFnZ3J6c3hxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3MzA5ODgsImV4cCI6MjA1OTMwNjk4OH0.a12c2LIuIH_f2GFF1BUy823EqY3jm0mxJWyk1hkT0xk';

  try {
    // 🔍 Check if the slug already exists
    const getRes = await fetch(`${SUPABASE_URL}/rest/v1/views?slug=eq.${slug}`, {
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
        Prefer: 'return=representation',
      },
    });

    const data = await getRes.json();

    if (data.length > 0) {
      // ✏️ Update view count
      await fetch(`${SUPABASE_URL}/rest/v1/views?slug=eq.${slug}`, {
        method: 'PATCH',
        headers: {
          apikey: SUPABASE_ANON_KEY,
          Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ views: data[0].views + 1 }),
      });
    } else {
      // ➕ Create new view record
      await fetch(`${SUPABASE_URL}/rest/v1/views`, {
        method: 'POST',
        headers: {
          apikey: SUPABASE_ANON_KEY,
          Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ slug, views: 1 }),
      });
    }

    return new Response(JSON.stringify({ status: 'ok' }), { status: 200 });
  } catch (error) {
    console.error('View tracking error:', error);
    return new Response(JSON.stringify({ error: 'Server error' }), { status: 500 });
  }
}
