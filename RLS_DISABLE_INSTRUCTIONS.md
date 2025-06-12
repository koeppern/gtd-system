# RLS Disable Instructions for GTD Tables

Since automatic RLS disabling through scripts is encountering connection issues, please follow these manual steps to disable RLS on GTD tables for testing purposes.

## Method 1: Supabase Dashboard (Recommended)

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Navigate to your project: `jgfkritnfowuylobbpqu`

2. **Open SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New query"

3. **Execute RLS Disable Commands**
   Copy and paste the following SQL commands:

   ```sql
   -- Disable RLS on all GTD tables for testing
   ALTER TABLE gtd_projects DISABLE ROW LEVEL SECURITY;
   ALTER TABLE gtd_tasks DISABLE ROW LEVEL SECURITY;
   ALTER TABLE gtd_fields DISABLE ROW LEVEL SECURITY;
   ALTER TABLE gtd_users DISABLE ROW LEVEL SECURITY;
   
   -- Verify RLS status
   SELECT 
       schemaname,
       tablename,
       rowsecurity
   FROM pg_tables 
   WHERE tablename IN ('gtd_projects', 'gtd_tasks', 'gtd_fields', 'gtd_users')
   ORDER BY tablename;
   ```

4. **Click "Run" to execute**

## Method 2: psql Command Line (If available)

If you have PostgreSQL client tools installed:

```bash
# Use the database URL from .env file
psql "postgresql://postgres.jgfkritnfowuylobbpqu:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpnZmtyaXRuZm93dXlsb2JicHF1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTQ4ODg1NywiZXhwIjoyMDY1MDY0ODU3fQ.5lxQORHj_JlVj6pSQj3inXUORZbRRXa1DVyatd_lRMQ@aws-0-us-east-1.pooler.supabase.com:5432/postgres" -c "ALTER TABLE gtd_projects DISABLE ROW LEVEL SECURITY;"

# Repeat for other tables...
```

## Expected Results

After running the commands, you should see:
- `ALTER TABLE` responses for each table
- Verification query showing `rowsecurity = false` for all GTD tables

## ⚠️ Security Warning

**IMPORTANT**: RLS is being disabled temporarily for testing purposes only.

- This removes access controls on GTD tables
- Any authenticated user will be able to access all data
- **REMEMBER** to re-enable RLS after testing

## Re-enabling RLS After Testing

When testing is complete, re-enable RLS with:

```sql
-- Re-enable RLS on all GTD tables
ALTER TABLE gtd_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE gtd_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE gtd_fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE gtd_users ENABLE ROW LEVEL SECURITY;
```

## Troubleshooting

If tables don't exist:
1. Check if ETL scripts have been run to create and populate tables
2. Verify database connection settings in `.env` file
3. Run: `python src/etl_projects.py --force` and `python src/etl_tasks.py --force`

## Files Created for Reference

- `/mnt/c/python/gtd/disable_rls_manual.sql` - SQL commands to disable RLS
- `/mnt/c/python/gtd/enable_rls_manual.sql` - SQL commands to re-enable RLS
- `/mnt/c/python/gtd/src/backend/scripts/disable_rls_*.py` - Various automated scripts (connection issues)

## Next Steps After RLS Disable

1. Run FastAPI backend tests
2. Test API endpoints without RLS restrictions
3. Debug any remaining authentication/authorization issues
4. **Re-enable RLS when testing is complete**