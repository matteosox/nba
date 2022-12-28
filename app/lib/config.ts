export default {
    awsS3Region: "us-west-2",
    awsS3Bucket: "nba-mattefay",
    awsS3RootKey: "prod",
    awsAccessKeyId: process.env.AccessKeyId,
    awsSecretAccessKey: process.env.SecretAccessKey,
    useLocal: !!process.env.USE_LOCAL
}
