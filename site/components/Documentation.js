import Head from 'next/head'


export default function Documentation() {
    return (
        <div className={styles.container}>
            <Head>
                <title>Documentation - DataPi</title>
                <meta name="description" content="DataPi documentation" />
                <link rel="icon" href="/favicon.ico" />
            </Head>

            <main className={styles.main}>
                <h1 className={styles.title}>
                    Documentation
                </h1>

                <p className={styles.description}>
                    Welcome to the DataPi documentation.
                </p>

                {/* Add more documentation content here */}
            </main>
        </div>
    )
}