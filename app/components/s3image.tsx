import Image from 'next/image'
import { AWS_S3_REGION, AWS_S3_BUCKET, AWS_S3_ROOT_KEY } from '../lib/constants'

function S3Loader({ src }: { src: string }) {
  return `https://${AWS_S3_BUCKET}.s3-${AWS_S3_REGION}.amazonaws.com/${AWS_S3_ROOT_KEY}${src}`
}

export default function S3Image({
  src,
  width,
  height,
  ...props
}: {
  src: string,
  width: number | string,
  height: number | string,
}) {
  return (
    <Image
      loader={S3Loader}
      src={src}
      width={width}
      height={height}
      {...props}
    />
  )
}
