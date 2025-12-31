import { NextResponse } from 'next/server'
import { promises as fs } from 'fs'
import path from 'path'
import archiver from 'archiver'

export async function GET() {
  try {
    // Extension is now in the public folder
    const extensionPath = path.join(process.cwd(), 'public', 'extension')
    
    // Check if extension exists
    try {
      await fs.access(extensionPath)
      console.log('Found extension at:', extensionPath)
    } catch {
      console.error('Extension folder not found at:', extensionPath)
      return NextResponse.json(
        { 
          error: 'Extension folder not found',
          path: extensionPath,
          cwd: process.cwd()
        },
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
      
      // Add the extension directory to the archive at root level (false = no parent folder)
      archive.directory(extensionPath, false)
      
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
      { error: 'Failed to create extension package', details: String(error) },
      { status: 500 }
    )
  }
}
