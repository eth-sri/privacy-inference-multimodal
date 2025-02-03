"use client";

import Image from "next/image";

interface Props {
  imageUrl?: string;
}

export function ImageLink({ imageUrl }: Props) {
  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <a
        className="pointer-events-none flex place-items-center gap-2 p-8 lg:pointer-events-auto lg:p-0"
        href={imageUrl}
        target="_blank"
        rel="noopener noreferrer"
      >
        <Image
          fill={true}
          style={{ objectFit: "contain" }}
          src={imageUrl || "/something"}
          alt="Some image"
        />
      </a>
    </div>
  );
}
