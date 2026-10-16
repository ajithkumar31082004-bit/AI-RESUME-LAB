#!/bin/bash
# ==============================================================================
# AI RESUME LAB — S3 Static Website Deployment Script
# Syncs frontend files to Amazon S3 Bucket configured for static website hosting.
# ==============================================================================

set -e

# Configuration (Default bucket: s3-ajith-3108)
BUCKET_NAME="${1:-s3-ajith-3108}"
REGION="${2:-us-east-1}"
FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../frontend" && pwd)"

echo "🚀 Deploying AI Resume Lab Frontend to S3..."
echo "📂 Source Directory: $FRONTEND_DIR"
echo "🪣 Target S3 Bucket: s3://$BUCKET_NAME"
echo "🌍 AWS Region: $REGION"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# 1. Sync HTML, JS, CSS files to S3
echo "📤 Uploading static assets..."
aws s3 sync "$FRONTEND_DIR" "s3://$BUCKET_NAME" \
    --region "$REGION" \
    --delete \
    --exclude ".git/*" \
    --exclude "*.DS_Store"

# 2. Set specific Content-Type headers for web caching
echo "⚙️ Setting Cache-Control headers for CSS and JS..."
aws s3 cp "$FRONTEND_DIR/css" "s3://$BUCKET_NAME/css" \
    --recursive \
    --region "$REGION" \
    --content-type "text/css" \
    --metadata-directive REPLACE

aws s3 cp "$FRONTEND_DIR/js" "s3://$BUCKET_NAME/js" \
    --recursive \
    --region "$REGION" \
    --content-type "application/javascript" \
    --metadata-directive REPLACE

echo "✅ Frontend successfully deployed to S3!"
echo "🔗 Website URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
