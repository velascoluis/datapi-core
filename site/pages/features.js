import styles from '../styles/Features.module.css';
import Image from 'next/image';

export default function FeaturesPage() {
    const features = [
        {
            title: 'Static Analysis',
            description: 'Debug 20x faster with static analysis. Identify errors in your models without running them in the cloud.',
            image: '/images/feature1.png',
        },
        {
            title: 'dataPi Types',
            description: 'Elevate your models with user-defined types. Prevent logic errors and validate your code with a type system.',
            image: '/images/feature2.png',
        },
        // Add more features as needed
    ];

    return (
        <section className={styles.featuresSection}>
            <h2>Key Features</h2>
            <div className={styles.featureList}>
                {features.map((feature, index) => (
                    <div key={index} className={styles.feature}>
                        <Image src={feature.image} alt={feature.title} width={100} height={100} />
                        <h3>{feature.title}</h3>
                        <p>{feature.description}</p>
                    </div>
                ))}
            </div>
        </section>
    );
}