import { NextResponse } from 'next/server'
import { promises as fs } from 'fs'
import path from 'path'
import archiver from 'archiver'

export async function GET() {
  try {
    // Try multiple possible paths for the extension folder
    const possiblePaths = [
      path.join(process.cwd(), '..', 'backend', 'extension'),  // Vercel monorepo structure
      path.join(process.cwd(), 'backend', 'extension'),         // If deployed from root
      path.join(process.cwd(), '..', 'extension'),              // Alternative structure
      path.join(process.cwd(), 'extension'),                    // Direct structure
    ]
    
    let extensionPath: string | null = null
    
    // Find the first existing path
    for (const testPath of possiblePaths) {
      try {
        await fs.access(testPath)
        extensionPath = testPath
        console.log('Found extension at:', testPath)
        break
      } catch {
        console.log('Extension not found at:', testPath)
      }
    }
    
    if (!extensionPath) {
      console.error('Extension folder not found in any location')
      console.error('CWD:', process.cwd())
      console.error('Tried paths:', possiblePaths)
      return NextResponse.json(
        { 
          error: 'Extension folder not found',
          cwd: process.cwd(),
          triedPaths: possiblePaths 
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
      
      // Add the extension directory to the archive
      archive.directory(extensionPath!, 'scamcap-extension')
      
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
