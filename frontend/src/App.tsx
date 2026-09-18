import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { AppShell, Alert, Box, Button, Group, LoadingOverlay, MantineProvider, createTheme } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import { IconAlertTriangle, IconRefresh } from '@tabler/icons-react';

import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { IngestionView } from './components/IngestionView';
import { ReaderWorkspace } from './components/ReaderWorkspace';
import { AccessibilityDrawer, DEFAULT_SETTINGS } from './components/AccessibilityDrawer';
import { SourceAnchorDrawer } from './components/SourceAnchorDrawer';
import { FocusRuler } from './components/FocusRuler';
import type { AccessibilitySettings, ReadingBlock, ThemePalette, TransformationResponse } from './types';
import { resolveFontStack, resolvePalette } from './types';
import { ApiError, checkHealth, transformAcademicText } from './utils/api';

export default function App() {
  const [data, setData] = useState<TransformationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [rawText, setRawText] = useState<string>('');
  const [progress, setProgress] = useState<number>(0);
  const [backendNotice, setBackendNotice] = useState<string | null>(null);

  const [settingsOpened, setSettingsOpened] = useState<boolean>(false);
  const [sourceBlock, setSourceBlock] = useState<ReadingBlock | null>(null);

  const [settings, setSettings] = useState<AccessibilitySettings>({ ...DEFAULT_SETTINGS });

  const abortRef = useRef<AbortController | null>(null);
  const resultsRef = useRef<HTMLDivElement | null>(null);

  const palette: ThemePalette = useMemo(
    () => resolvePalette(settings.colorTheme),
    [settings.colorTheme]
  );

  const fontStack = useMemo(() => resolveFontStack(settings.fontFamily), [settings.fontFamily]);

  const theme = useMemo(
    () =>
      createTheme({
        fontFamily: fontStack,
        headings: { fontFamily: fontStack },
        primaryColor: 'indigo',
      }),
    [fontStack]
  );

  // Pre-flight: warn early when the backend has no API key or is unreachable,
  // so the user is not surprised after pasting a 10,000 character document.
  useEffect(() => {
    const controller = new AbortController();
    checkHealth(controller.signal)
      .then((health) => {
        if (!health.api_key_configured) {
          setBackendNotice(
            'The backend is running but has no OPENAI_API_KEY configured. Add it to backend/.env and restart the server.'
          );
        } else {
          setBackendNotice(null);
        }
      })
      .catch(() => {
        setBackendNotice(
          'The Cognita backend is not reachable. Start it with: cd backend && uvicorn main:app --reload --port 8000'
        );
      });
    return () => controller.abort();
  }, []);

  const handleTransform = useCallback(async (textToProcess: string) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);
    setProgress(0);
    setRawText(textToProcess);

    try {
      const result = await transformAcademicText(textToProcess, controller.signal);
      setData(result);
      window.setTimeout(
        () => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
        80
      );
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return;
      const message =
        err instanceof ApiError
          ? err.message
          : 'An unexpected client error occurred while transforming the document.';
      setError(message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleReset = useCallback(() => {
    abortRef.current?.abort();
    setData(null);
    setRawText('');
    setError(null);
    setProgress(0);
    setSourceBlock(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  return (
    <MantineProvider
      theme={theme}
      forceColorScheme={settings.colorTheme === 'dark' ? 'dark' : 'light'}
    >
      <Notifications position="top-right" limit={3} />

      <Box
        style={{
          backgroundColor: palette.background,
          color: palette.text,
          minHeight: '100vh',
          fontFamily: fontStack,
          letterSpacing: `${settings.letterSpacing}em`,
          transition: 'background-color 150ms ease',
        }}
      >
        {settings.focusRuler && <FocusRuler />}

        <AppShell header={{ height: 66 }} padding="md">
          <AppShell.Header
            style={{
              backgroundColor: palette.background,
              borderBottom: `1px solid ${palette.border}`,
            }}
          >
            <Header
              hasData={Boolean(data)}
              progress={progress}
              palette={palette}
              onOpenSettings={() => setSettingsOpened(true)}
              onReset={handleReset}
            />
          </AppShell.Header>

          <AppShell.Main style={{ paddingBottom: 0 }}>
            <LoadingOverlay
              visible={loading}
              zIndex={300}
              overlayProps={{ blur: 3, backgroundOpacity: 0.45 }}
              loaderProps={{ color: 'indigo', type: 'dots' }}
            />

            {data && <div ref={resultsRef} />}

            {error && (
              <Alert
                color="red"
                variant="light"
                icon={<IconAlertTriangle size={18} />}
                title="Transformation failed"
                mb="lg"
                className="cognita-workspace"
              >
                <Group justify="space-between" align="center" wrap="wrap">
                  <span>{error}</span>
                  <Button
                    size="xs"
                    variant="light"
                    color="red"
                    leftSection={<IconRefresh size={14} />}
                    onClick={() => rawText && handleTransform(rawText)}
                    disabled={!rawText}
                  >
                    Retry
                  </Button>
                </Group>
              </Alert>
            )}

            {!data && backendNotice && (
              <Alert
                color="yellow"
                variant="light"
                icon={<IconAlertTriangle size={18} />}
                title="Backend check"
                mb="lg"
                className="cognita-workspace"
              >
                {backendNotice}
              </Alert>
            )}

            {data ? (
              <ReaderWorkspace
                data={data}
                sourceText={rawText}
                settings={settings}
                palette={palette}
                onInspectSource={(block) => setSourceBlock(block)}
                onProgress={setProgress}
              />
            ) : (
              <IngestionView
                isLoading={loading}
                palette={palette}
                onTransform={handleTransform}
              />
            )}

            <Box className="cognita-workspace">
              <Footer palette={palette} />
            </Box>

            <AccessibilityDrawer
              opened={settingsOpened}
              onClose={() => setSettingsOpened(false)}
              settings={settings}
              palette={palette}
              onUpdateSettings={setSettings}
            />

            <SourceAnchorDrawer
              opened={Boolean(sourceBlock)}
              onClose={() => setSourceBlock(null)}
              anchorText={sourceBlock?.source_citation_anchor ?? ''}
              blockHeadline={sourceBlock?.headline}
              fullOriginalText={rawText}
              palette={palette}
            />
          </AppShell.Main>
        </AppShell>
      </Box>
    </MantineProvider>
  );
}
