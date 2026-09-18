import React, { useMemo, useState } from 'react';
import {
  Alert,
  Badge,
  Box,
  Button,
  Card,
  Divider,
  Group,
  Paper,
  Progress,
  SimpleGrid,
  Stack,
  Text,
  Textarea,
  Title,
} from '@mantine/core';
import {
  IconAlertTriangle,
  IconBook2,
  IconMoodSearch,
  IconSparkles,
  IconWand,
} from '@tabler/icons-react';

import { SAMPLE_DOCUMENTS, type SampleDocument } from '../utils/samples';
import { countWords, predictComplexity } from '../utils/anchor';
import type { ThemePalette } from '../types';

const MIN_CHARS = 100;
const MAX_CHARS = 50000;

interface Props {
  isLoading: boolean;
  palette: ThemePalette;
  onTransform: (text: string) => void;
}

export const IngestionView: React.FC<Props> = ({ isLoading, palette, onTransform }) => {
  const [text, setText] = useState<string>('');

  const stats = useMemo(() => {
    const words = countWords(text);
    const complexity = predictComplexity(text);
    const readingMinutes = words > 0 ? Math.max(1, Math.round(words / 200)) : 0;
    return { words, complexity, readingMinutes };
  }, [text]);

  const length = text.trim().length;
  const tooShort = length > 0 && length < MIN_CHARS;
  const tooLong = length > MAX_CHARS;
  const canSubmit = length >= MIN_CHARS && !tooLong && !isLoading;

  const loadSample = (sample: SampleDocument) => {
    setText(sample.text);
  };

  return (
    <Box className="cognita-workspace">
      <Stack gap="lg">
        <Box>
          <Title order={1} size="h2" mb={4}>
            Restructure dense academic text for focused reading
          </Title>
          <Text c={palette.mutedText} size="sm" maw={720}>
            Paste a journal article, textbook chapter, or case note. Cognita preserves the
            original terminology and nuance while breaking monolithic prose into paced,
            verifiable reading blocks.
          </Text>
        </Box>

        <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="sm">
          {SAMPLE_DOCUMENTS.map((sample) => (
            <Card
              key={sample.id}
              withBorder
              radius="md"
              padding="sm"
              style={{ backgroundColor: palette.surface, borderColor: palette.border }}
            >
              <Group justify="space-between" mb={4} wrap="nowrap">
                <Badge size="xs" variant="light" color="indigo">
                  {sample.subject}
                </Badge>
                <IconBook2 size={15} color={palette.accent} aria-hidden />
              </Group>
              <Text fw={600} size="sm" mb={4}>
                {sample.title}
              </Text>
              <Text size="xs" c={palette.mutedText} mb="sm" lineClamp={3}>
                {sample.description}
              </Text>
              <Button
                size="compact-xs"
                variant="light"
                color="indigo"
                onClick={() => loadSample(sample)}
                disabled={isLoading}
              >
                Load sample
              </Button>
            </Card>
          ))}
        </SimpleGrid>

        <Card
          withBorder
          radius="md"
          padding="lg"
          style={{ backgroundColor: palette.surface, borderColor: palette.border }}
        >
          <Textarea
            label="Raw academic text"
            description={`Minimum ${MIN_CHARS} characters, maximum ${MAX_CHARS.toLocaleString()} characters per transformation.`}
            placeholder="Paste the unfiltered academic passage here..."
            value={text}
            onChange={(event) => setText(event.currentTarget.value)}
            onKeyDown={(event) => {
              // Ctrl/Cmd + Enter submits without forcing a mouse trip.
              if ((event.ctrlKey || event.metaKey) && event.key === 'Enter' && canSubmit) {
                onTransform(text.trim());
              }
            }}
            autosize
            minRows={12}
            maxRows={26}
            error={tooShort ? `Add at least ${MIN_CHARS} characters of source material.` : null}
            styles={{
              input: {
                backgroundColor: palette.background,
                color: palette.text,
                fontSize: 15,
                lineHeight: 1.7,
              },
            }}
          />

          <Group justify="space-between" mt="sm" gap="xs">
            <Group gap="xs">
              <Badge variant="light" color="gray" size="sm">
                {stats.words.toLocaleString()} words
              </Badge>
              <Badge variant="light" color="gray" size="sm">
                {length.toLocaleString()} / {MAX_CHARS.toLocaleString()} chars
              </Badge>
              <Badge
                variant="light"
                color={stats.complexity >= 7 ? 'red' : stats.complexity >= 4 ? 'orange' : 'gray'}
                size="sm"
                leftSection={<IconMoodSearch size={12} />}
              >
                Complexity {stats.complexity}/10
              </Badge>
              {stats.words > 0 && (
                <Badge variant="light" color="gray" size="sm">
                  ~{stats.readingMinutes} min at 200 WPM
                </Badge>
              )}
            </Group>
          </Group>

          {tooLong && (
            <Alert color="red" icon={<IconAlertTriangle size={16} />} mt="sm" title="Text too long">
              Split the document and transform it in parts — the backend rejects payloads above{' '}
              {MAX_CHARS.toLocaleString()} characters to protect the token window.
            </Alert>
          )}

          <Progress
            value={Math.min(100, (length / MAX_CHARS) * 100)}
            size="xs"
            mt="md"
            color={tooLong ? 'red' : 'indigo'}
            aria-label="Input size relative to the maximum supported length"
          />

          <Divider my="lg" />

          <Group justify="space-between" align="center">
            <Text size="xs" c={palette.mutedText} maw={420}>
              Your text is sent to the configured OpenAI-compatible endpoint for restructuring.
              Nothing is stored on the server. Press <strong>Ctrl/Cmd + Enter</strong> to submit.
            </Text>
            <Button
              size="md"
              leftSection={<IconWand size={18} />}
              loading={isLoading}
              disabled={!canSubmit}
              onClick={() => onTransform(text.trim())}
              color="indigo"
            >
              Restructure for Focus
            </Button>
          </Group>
        </Card>

        <Paper
          withBorder
          radius="md"
          p="md"
          style={{ borderColor: palette.border, backgroundColor: 'transparent' }}
        >
          <Group gap="xs" align="flex-start" wrap="nowrap">
            <IconSparkles size={16} color={palette.accent} style={{ marginTop: 3 }} aria-hidden />
            <Text size="xs" c={palette.mutedText}>
              Cognita is a cognitive scaffolding lens, not an exam substitute. Every generated
              block keeps a verbatim anchor into your original text so you can verify claims
              before relying on them.
            </Text>
          </Group>
        </Paper>
      </Stack>
    </Box>
  );
};
