import { NextResponse } from 'next/server'
import { promises as fs } from 'fs'
import path from 'path'
import archiver from 'archiver'
import { Readable } from 'stream'

export async function GET() {
  try {
    // Path to the extension folder (go up from frontend to root, then to extension)
    const extensionPath = path.join(process.cwd(), '..', 'extension')
    
    // Check if extension folder exists
    try {
      await fs.access(extensionPath)
    } catch {
      return NextResponse.json(
        { error: 'Extension folder not found' },
        { status: 404 }
      )
    }

    // Create a buffer to store the zip
    const chunks: Buffer[] = []
    
    // Create archiver instance
    const archive = archiver('zip', {
      zlib: { level: 9 } // Maximum compression
    })

    // Collect chunks
    archive.on('data', (chunk: Buffer) => chunks.push(chunk))
    
    // Wait for archive to finish
    await new Promise<void>((resolve, reject) => {
      archive.on('end', () => resolve())
      archive.on('error', (err: Error) => reject(err))
      
      // Add the extension directory to the archive
      archive.directory(extensionPath, 'scamcap-extension')
      
      // Finalize the archive
      archive.finalize()
    })

    // Combine all chunks
    const zipBuffer = Buffer.concat(chunks)

    // Return the zip file
    return new NextResponse(zipBuffer, {
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename="scamcap-extension.zip"',
        'Content-Length': zipBuffer.length.toString(),
      },
    })
  } catch (error) {
    console.error('Error creating zip:', error)
    return NextResponse.json(
      { error: 'Failed to create extension package' },
      { status: 500 }
    )
  }
}
