import * as constants from '../lib/constants'
import { S3Client, GetObjectCommand, ListObjectsV2Command } from '@aws-sdk/client-s3'
import { Readable } from "stream"

const clients = new Proxy({}, {
  get: function (target: { [key: string]: S3Client}, region: string) {
    if (!(region in target)) {
      target[region] = new S3Client({ region, credentials: getCredentials })
    }
    return target[region]
  }
})

async function getCredentials() {
  return {
    accessKeyId: constants.AWS_ACCESS_KEY_ID,
    secretAccessKey: constants.AWS_SECRET_ACCESS_KEY,
  }
}

export async function listKeys({ region, bucket, prefix }: {region: string, bucket: string, prefix?: string}) {
  const s3 = clients[region]
  let continuationToken: string
  const bucketParams = { Bucket: bucket, Prefix: prefix, ContinuationToken: continuationToken}
  let truncated = true
  let keys: string[] = []
  while (truncated) {
    const response = await s3.send(new ListObjectsV2Command(bucketParams))
    keys.push(...response.Contents.map((item) => item.Key))
    truncated = response.IsTruncated
    bucketParams.ContinuationToken = response.NextContinuationToken
  }
  return keys
}

async function readStream(stream: Readable) {
  const chunks: Buffer[] = []
  for await (let chunk of stream) {
      chunks.push(Buffer.from(chunk))
  }
  return Buffer.concat(chunks).toString("utf-8")
}

interface S3Object {
  region: string
  bucket: string
  key: string
}

export async function getObjectStream({ region, bucket, key }: S3Object) {
  const s3 = clients[region]
  const params = {
    Bucket: bucket,
    Key: key,
  }
  const response = await s3.send(new GetObjectCommand(params))
  return response.Body as Readable
}

export async function getObjectString(input: S3Object) {
  return readStream(await getObjectStream(input))
}
