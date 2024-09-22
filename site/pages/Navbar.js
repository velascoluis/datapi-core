import Link from 'next/link';

export default function Navbar() {
    return (
        <nav className="bg-white py-4 shadow-md">
            <div className="container mx-auto px-4 flex justify-between items-center">
                <Link href="/">
                    <a className="text-blue-500 font-bold text-xl">My Website</a>
                </Link>
                <ul className="flex space-x-6">
                    <li>
                        <Link href="/features">
                            <a className="hover:text-blue-600">Features</a>
                        </Link>
                    </li>
                    <li>
                        <Link href="/benefits">
                            <a className="hover:text-blue-600">Benefits</a>
                        </Link>
                    </li>
                    <li>
                        <Link href="/testimonials">
                            <a className="hover:text-blue-600">Testimonials</a>
                        </Link>
                    </li>
                    <li>
                        <Link href="/pricing">
                            <a className="hover:text-blue-600">Pricing</a>
                        </Link>
                    </li>
                    <li>
                        <Link href="/resources">
                            <a className="hover:text-blue-600">Resources</a>
                        </Link>
                    </li>
                    <li>
                        <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600">
                            Get Started
                        </button>
                    </li>
                </ul>
            </div>
        </nav>
    );
}