# Daily Heavens Deployment Guide

This guide describes how to deploy the Daily Heavens application to Vercel and connect it to Supabase.

## Architecture Overview

The Daily Heavens application consists of:

1. **Frontend**: Next.js application deployed to Vercel
2. **Unified API Service**: FastAPI-based API that handles birth chart calculation and interpretation
3. **Database**: Supabase PostgreSQL database for storing user data and chart results

## Prerequisites

- Vercel account
- Supabase account
- GitHub repository with your code
- Git installed on your local machine

## Step 1: Supabase Setup

1. Create a new Supabase project for "Daily Heavens"
2. Set up the `form_submissions` table with the SQL:

```sql
CREATE TABLE form_submissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT NOT NULL,
  date_of_birth DATE NOT NULL,
  time_of_birth TIME,
  place_of_birth TEXT,
  sun_sign TEXT,
  moon_sign TEXT,
  ascendant_sign TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  processed BOOLEAN DEFAULT FALSE,
  birth_chart_data JSONB,
  interpretation_data JSONB
);

-- Create an index on email for faster lookups
CREATE INDEX form_submissions_email_idx ON form_submissions(email);
```

3. Get your Supabase URL and API keys from the Supabase dashboard:
   - Go to Project Settings > API
   - Copy the values for URL, anon key, and service role key

## Step 2: Vercel Setup

### Install Vercel CLI (Optional)

```bash
npm i -g vercel
vercel login
```

### Configure Environment Variables

Add the following environment variables to your Vercel project:

```
NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
```

### Deploy from Git Repository

1. Connect your GitHub repository to Vercel:
   - Go to the Vercel dashboard
   - Click "Add New Project"
   - Import your GitHub repository
   - Configure the project settings (build command, output directory, etc.)

2. Set Environment Variables:
   - Add the environment variables mentioned above
   - Click "Deploy"

3. Configure build settings:
   - Build Command: `npm run build` or `pnpm build`
   - Output Directory: `.next`
   - Install Command: `npm install` or `pnpm install`

## Step 3: Testing the Deployment

1. Test the frontend by opening the deployed URL
2. Test the API by sending a request to `/api/birth-chart`
3. Verify the data is being saved to Supabase

## Troubleshooting

### Common Issues and Solutions

#### Missing Environment Variables
If you see an error related to Supabase connection, check that your environment variables are correctly set in Vercel.

#### API Timeout
If the API times out, you may need to increase the execution time limit for the API functions in your Vercel configuration.

#### Missing Planets in Birth Chart
If outer planets (Uranus, Neptune, Pluto) are missing, the current implementation is designed to handle this gracefully.

#### Interpretation Errors
If you see errors in the interpretation, check the logs and verify that the birth chart data is being correctly passed to the interpretation service.

## Maintenance

### Monitoring
- Check Vercel Analytics for API usage and errors
- Regularly monitor Supabase database size and query performance

### Updating
To update the deployed application:
1. Push changes to your GitHub repository
2. Vercel will automatically deploy the updated version

## Security Considerations

- Never expose the Supabase service role key to the client
- Use row-level security (RLS) in Supabase to protect user data
- Use HTTPS for all API requests
- Validate all user inputs

## Conclusion

Your Daily Heavens application should now be deployed and connected to Supabase. If you encounter any issues, check the logs in Vercel and Supabase for more information. 