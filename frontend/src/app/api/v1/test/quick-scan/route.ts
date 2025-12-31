import { NextResponse } from 'next/server';

// Simple phishing detection logic
function analyzeUrl(url: string) {
  const suspiciousPatterns = [
    /login/i,
    /verify/i,
    /account/i,
    /secure/i,
    /update/i,
    /confirm/i,
    /banking/i,
    /paypal/i,
    /-/g // Multiple hyphens
  ];

  let riskScore = 0;
  const indicators: string[] = [];

  // Check for suspicious patterns
  suspiciousPatterns.forEach(pattern => {
    if (pattern.test(url)) {
      riskScore += 0.15;
      indicators.push(`Suspicious pattern detected: ${pattern}`);
    }
  });

  // Check for IP address instead of domain
  if (/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(url)) {
    riskScore += 0.3;
    indicators.push('URL uses IP address instead of domain name');
  }

  // Check for excessive subdomains
  const domain = url.replace(/https?:\/\//, '').split('/')[0];
  const subdomains = domain.split('.').length - 2;
  if (subdomains > 2) {
    riskScore += 0.2;
    indicators.push('Excessive subdomains detected');
  }

  // Ensure risk score doesn't exceed 1
  riskScore = Math.min(riskScore, 1);

  // Determine risk level
  let riskLevel = 'low';
  if (riskScore >= 0.7) {
    riskLevel = 'critical';
  } else if (riskScore >= 0.5) {
    riskLevel = 'high';
  } else if (riskScore >= 0.3) {
    riskLevel = 'medium';
  }

  return {
    url,
    is_safe: riskScore < 0.5,
    risk_score: riskScore,
    risk_level: riskLevel,
    indicators: indicators.length > 0 ? indicators : ['No immediate threats detected'],
    timestamp: new Date().toISOString()
  };
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const url = searchParams.get('url');

    if (!url) {
      return NextResponse.json(
        { error: 'URL parameter is required' },
        { status: 400 }
      );
    }

    const result = analyzeUrl(url);
    return NextResponse.json(result);
  } catch (error) {
    console.error('Quick scan error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { url } = body;

    if (!url) {
      return NextResponse.json(
        { error: 'URL is required in request body' },
        { status: 400 }
      );
    }

    const result = analyzeUrl(url);
    return NextResponse.json(result);
  } catch (error) {
    console.error('Quick scan error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
