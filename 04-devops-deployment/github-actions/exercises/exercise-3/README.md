# Exercise 3: Deployment Pipeline

## Objective

Create a complete deployment pipeline with staging and production environments, including approval gates.

## Requirements

1. **Environments**
   - `staging`: Auto-deploy on push to main
   - `production`: Require manual approval

2. **Pipeline stages**
   - Build and test
   - Deploy to staging
   - Run smoke tests on staging
   - Deploy to production (with approval)

3. **Features**
   - Environment-specific secrets
   - Deployment URLs in GitHub UI
   - Rollback capability

## Starting Files

- `deploy.yml` - Incomplete deployment workflow
- `Dockerfile` - Application Dockerfile
- `deploy.sh` - Deployment script

## Steps

1. Configure environments (staging and production)

2. Add deployment jobs with environment protection

3. Implement smoke tests between staging and production

4. Add manual approval for production deployment

## Environment Configuration (in GitHub)

Before the workflow works, configure in GitHub:
1. Go to Settings > Environments
2. Create `staging` environment
3. Create `production` environment with:
   - Required reviewers
   - Wait timer (optional)
   - Deployment branch restriction

## Expected Pipeline Flow

```
build ──► test ──► deploy-staging ──► smoke-test ──► deploy-production
                                                          │
                                                    [Manual Approval]
```

## Success Criteria

- [ ] Staging deploys automatically on push
- [ ] Smoke tests run after staging deploy
- [ ] Production requires manual approval
- [ ] Environment URLs visible in GitHub UI
- [ ] Secrets scoped to environments
