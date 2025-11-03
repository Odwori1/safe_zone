#!/usr/bin/env python3
"""
Check S3 configuration and test uploads endpoint
"""
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

def check_s3_config():
    print("🔧 CHECKING S3 CONFIGURATION")
    print("=" * 35)
    
    # Check environment variables
    s3_config = {
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION': os.getenv('AWS_REGION'),
        'S3_BUCKET': os.getenv('S3_BUCKET')
    }
    
    print("S3 Configuration:")
    for key, value in s3_config.items():
        if 'SECRET' in key or 'KEY' in key:
            print(f"   {key}: {'✅ SET' if value and value != 'your_secret_key_here' else '❌ NOT SET'}")
        else:
            print(f"   {key}: {value if value else '❌ NOT SET'}")
    
    # Test S3 connection if credentials are set
    if (s3_config['AWS_ACCESS_KEY_ID'] and 
        s3_config['AWS_SECRET_ACCESS_KEY'] and
        s3_config['AWS_ACCESS_KEY_ID'] != 'your_access_key_here' and
        s3_config['AWS_SECRET_ACCESS_KEY'] != 'your_secret_key_here'):
        
        print("\nTesting S3 connection...")
        try:
            session = boto3.Session(
                aws_access_key_id=s3_config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=s3_config['AWS_SECRET_ACCESS_KEY'],
                region_name=s3_config['AWS_REGION']
            )
            
            s3 = session.client('s3')
            
            # Test list buckets (basic permission check)
            response = s3.list_buckets()
            print("✅ S3 connection successful!")
            print(f"   Available buckets: {len(response['Buckets'])}")
            
            # Check if target bucket exists
            if s3_config['S3_BUCKET']:
                try:
                    s3.head_bucket(Bucket=s3_config['S3_BUCKET'])
                    print(f"✅ Bucket '{s3_config['S3_BUCKET']}' exists and accessible")
                    
                    # Test presigned URL generation
                    try:
                        presigned_url = s3.generate_presigned_url(
                            'put_object',
                            Params={
                                'Bucket': s3_config['S3_BUCKET'],
                                'Key': 'test-file.txt'
                            },
                            ExpiresIn=3600
                        )
                        print("✅ Presigned URL generation successful")
                        print(f"   Sample URL: {presigned_url[:50]}...")
                    except Exception as e:
                        print(f"❌ Presigned URL generation failed: {e}")
                        
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == '404':
                        print(f"❌ Bucket '{s3_config['S3_BUCKET']}' does not exist")
                    elif error_code == '403':
                        print(f"❌ Access denied to bucket '{s3_config['S3_BUCKET']}'")
                    else:
                        print(f"❌ Bucket check failed: {e}")
            
        except NoCredentialsError:
            print("❌ No AWS credentials found")
        except ClientError as e:
            print(f"❌ AWS client error: {e}")
        except Exception as e:
            print(f"❌ S3 connection failed: {e}")
    else:
        print("\n❌ AWS credentials not configured or using placeholder values")
        print("💡 Update your .env file with real AWS credentials")
        print("   or configure AWS CLI with: aws configure")

if __name__ == "__main__":
    check_s3_config()
